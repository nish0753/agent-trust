// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract AgentTrust {
    address public owner;

    struct AgentProfile { string name; uint256 overallRep; uint256 tasksDone; bool registered; }
    struct SkillData    { uint256 totalScore; uint256 count; }
    struct Task         { uint256 taskId; address agent; uint256 score; string skill; uint256 timestamp; }

    mapping(address => AgentProfile)                 public agents;
    mapping(address => mapping(string => SkillData)) public skills;
    mapping(address => uint256)                      public verifierStake;
    Task[] public taskHistory;

    event AgentRegistered  (address indexed agent,    string name);
    event ReputationUpdated(address indexed agent,    uint256 newScore, string skill, uint256 taskId);
    event VerifierSlashed  (address indexed verifier, uint256 amount);

    modifier onlyOwner() { require(msg.sender == owner, "Not owner"); _; }

    constructor() { owner = msg.sender; }

    function registerAgent(address agent, string calldata name) external onlyOwner {
        agents[agent] = AgentProfile(name, 0, 0, true);
        emit AgentRegistered(agent, name);
    }

    function stakeAsVerifier() external payable {
        require(msg.value >= 0.01 ether, "Min 0.01 MON");
        verifierStake[msg.sender] += msg.value;
    }

    function finalizeTask(
        uint256 taskId, address agent, uint256 consensusScore,
        string  calldata skill,
        address[] calldata outliers, uint256 slashBps
    ) external onlyOwner {
        require(agents[agent].registered, "Agent not registered");

        skills[agent][skill].totalScore += consensusScore;
        skills[agent][skill].count      += 1;

        AgentProfile storage p = agents[agent];
        p.overallRep = ((p.overallRep * p.tasksDone) + consensusScore) / (p.tasksDone + 1);
        p.tasksDone  += 1;

        for (uint i = 0; i < outliers.length; i++) {
            uint256 slash = (verifierStake[outliers[i]] * slashBps) / 10_000;
            verifierStake[outliers[i]] -= slash;
            emit VerifierSlashed(outliers[i], slash);
        }

        taskHistory.push(Task(taskId, agent, consensusScore, skill, block.timestamp));
        emit ReputationUpdated(agent, p.overallRep, skill, taskId);
    }

    function getAgentProfile(address agent) external view
        returns (string memory, uint256, uint256) {
        AgentProfile storage p = agents[agent];
        return (p.name, p.overallRep, p.tasksDone);
    }

    function getSkillScore(address agent, string calldata skill) external view returns (uint256) {
        SkillData storage s = skills[agent][skill];
        return s.count == 0 ? 0 : s.totalScore / s.count;
    }
}
